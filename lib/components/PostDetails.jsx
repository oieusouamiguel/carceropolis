PostDetails = React.createClass({
  mixins: [ ReactMeteorData ],

  getMeteorData() {
    Meteor.subscribe('posts');

    return {
      post: Posts.findOne(this.props.id)
    };
  },

  render() {
    if (!this.data.post) { return false; }

    const post = this.data.post;
    const markup = {__html: post.content};

    // get the first image to be the post header background
    const titleImg = $(this.data.post.content).find('img').first();
    var headerStyle = {};
    if (titleImg.length > 0 ) {
      headerStyle['backgroundImage'] = "url('" + titleImg.attr("src") + "')";
    }

    return (
      <div className="post--details col-md-8 col-md-offset-2">
        <div className="post--header" style={headerStyle}></div>
        <div className="post--title"><h2>{post.title}</h2></div>
        <aside>
          por <span className="post--author">{post.username}</span>
          em <span className="post--time">{moment(post.createdAt).format('DD/MM/YYYY HH:MM')}</span>
        </aside>
        <div className="post--content" dangerouslySetInnerHTML={markup} />
      </div>
    );
  }
});